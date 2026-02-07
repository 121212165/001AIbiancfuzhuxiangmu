const natural = require('natural');
const { NlpManager } = require('node-nlp');
const nlp = require('compromise');
const winkNLP = require('wink-nlp');
const model = require('wink-eng-lite-web-model');
const fs = require('fs-extra');
const path = require('path');
const { createChunks } = require('./utils');

// 初始化winkNLP
const winkNlpInstance = winkNLP(model);
const its = winkNlpInstance.its;

/**
 * 文本向量化类
 */
class TextVectorizer {
  constructor(options = {}) {
    this.options = {
      language: 'en',
      stopwords: true,
      stemming: true,
      ...options
    };
    
    // 初始化TF-IDF向量化器
    this.tfidf = new natural.TfIdf();
    
    // 初始化NLP管理器
    this.nlpManager = new NlpManager({ 
      languages: [this.options.language],
      forceNER: true
    });
    
    // 停用词列表
    this.stopwords = new Set(natural.stopwords);
    
    // 词干提取器
    this.stemmer = natural.PorterStemmer;
  }
  
  /**
   * 预处理文本
   * @param {string} text 输入文本
   * @returns {string} 预处理后的文本
   */
  preprocess(text) {
    // 转换为小写
    let processedText = text.toLowerCase();
    
    // 移除标点符号
    processedText = processedText.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, ' ');
    
    // 移除多余空格
    processedText = processedText.replace(/\s{2,}/g, ' ').trim();
    
    return processedText;
  }
  
  /**
   * 分词
   * @param {string} text 输入文本
   * @returns {Array<string>} 分词结果
   */
  tokenize(text) {
    // 使用natural的分词器
    const tokenizer = new natural.WordTokenizer();
    let tokens = tokenizer.tokenize(text);
    
    // 过滤停用词
    if (this.options.stopwords) {
      tokens = tokens.filter(token => !this.stopwords.has(token));
    }
    
    // 词干提取
    if (this.options.stemming) {
      tokens = tokens.map(token => this.stemmer.stem(token));
    }
    
    return tokens;
  }
  
  /**
   * 提取关键词
   * @param {string} text 输入文本
   * @param {number} limit 关键词数量限制
   * @returns {Array<{term: string, score: number}>} 关键词列表
   */
  extractKeywords(text, limit = 10) {
    const doc = winkNlpInstance.readDoc(text);
    const tokens = doc.tokens().out(its.normal);
    
    // 使用TF-IDF计算关键词
    this.tfidf.addDocument(tokens);
    
    const keywords = [];
    this.tfidf.listTerms(0).forEach(item => {
      keywords.push({
        term: item.term,
        score: item.tfidf
      });
    });
    
    // 按得分排序并限制数量
    return keywords.sort((a, b) => b.score - a.score).slice(0, limit);
  }
  
  /**
   * 提取命名实体
   * @param {string} text 输入文本
   * @returns {Array<{entity: string, type: string}>} 命名实体列表
   */
  extractEntities(text) {
    const doc = winkNlpInstance.readDoc(text);
    const entities = doc.entities().out(its.detail);
    
    return entities.map(entity => ({
      entity: entity.text,
      type: entity.type
    }));
  }
  
  /**
   * 提取文本摘要
   * @param {string} text 输入文本
   * @param {number} sentenceCount 摘要句子数
   * @returns {string} 文本摘要
   */
  extractSummary(text, sentenceCount = 3) {
    const doc = winkNlpInstance.readDoc(text);
    const sentences = doc.sentences().out();
    
    if (sentences.length <= sentenceCount) {
      return sentences.join(' ');
    }
    
    // 简单的基于位置的摘要提取
    const summary = [];
    summary.push(sentences[0]); // 第一句通常很重要
    
    // 从中间部分选择句子
    const middleIndex = Math.floor(sentences.length / 2);
    summary.push(sentences[middleIndex]);
    
    // 最后一句通常也很重要
    if (sentenceCount >= 3) {
      summary.push(sentences[sentences.length - 1]);
    }
    
    return summary.join(' ');
  }
  
  /**
   * 生成文本向量表示
   * @param {string} text 输入文本
   * @returns {Object} 文本的向量表示
   */
  vectorize(text) {
    // 预处理文本
    const processedText = this.preprocess(text);
    
    // 分词
    const tokens = this.tokenize(processedText);
    
    // 提取关键词
    const keywords = this.extractKeywords(processedText, 20);
    
    // 提取实体
    const entities = this.extractEntities(processedText);
    
    // 提取摘要
    const summary = this.extractSummary(processedText, 3);
    
    // 使用compromise进行词性标注
    const tagged = nlp(processedText).json();
    
    return {
      tokens,
      keywords,
      entities,
      summary,
      tagged,
      metadata: {
        tokenCount: tokens.length,
        keywordCount: keywords.length,
        entityCount: entities.length
      }
    };
  }
  
  /**
   * 处理大型文本
   * @param {string} text 大型文本
   * @param {number} chunkSize 分块大小
   * @returns {Object} 合并后的向量表示
   */
  vectorizeLargeText(text, chunkSize = 10000) {
    // 将文本分割成块
    const chunks = createChunks(text, chunkSize);
    
    // 处理每个块
    const results = chunks.map(chunk => this.vectorize(chunk));
    
    // 合并结果
    const merged = {
      tokens: [],
      keywords: [],
      entities: [],
      summary: '',
      metadata: {
        tokenCount: 0,
        keywordCount: 0,
        entityCount: 0,
        chunkCount: chunks.length
      }
    };
    
    // 合并tokens (去重)
    const tokenSet = new Set();
    results.forEach(result => {
      result.tokens.forEach(token => tokenSet.add(token));
      merged.metadata.tokenCount += result.metadata.tokenCount;
    });
    merged.tokens = Array.from(tokenSet);
    
    // 合并关键词 (取前50个)
    const keywordMap = new Map();
    results.forEach(result => {
      result.keywords.forEach(kw => {
        const existing = keywordMap.get(kw.term);
        if (existing) {
          keywordMap.set(kw.term, { term: kw.term, score: existing.score + kw.score });
        } else {
          keywordMap.set(kw.term, kw);
        }
      });
      merged.metadata.keywordCount += result.metadata.keywordCount;
    });
    merged.keywords = Array.from(keywordMap.values())
      .sort((a, b) => b.score - a.score)
      .slice(0, 50);
    
    // 合并实体 (去重)
    const entityMap = new Map();
    results.forEach(result => {
      result.entities.forEach(entity => {
        entityMap.set(`${entity.entity}_${entity.type}`, entity);
      });
      merged.metadata.entityCount += result.metadata.entityCount;
    });
    merged.entities = Array.from(entityMap.values());
    
    // 合并摘要 (取第一个块的摘要)
    merged.summary = results[0].summary;
    
    return merged;
  }
  
  /**
   * 将向量化结果保存到文件
   * @param {Object} vectorData 向量化数据
   * @param {string} outputPath 输出文件路径
   * @returns {Promise<void>}
   */
  async saveVectorData(vectorData, outputPath) {
    await fs.writeJson(outputPath, vectorData, { spaces: 2 });
  }
}

/**
 * 将PDF内容向量化
 * @param {string} markdownContent Markdown内容
 * @param {string} outputPath 输出文件路径
 * @param {Object} options 选项
 * @returns {Promise<Object>} 向量化结果
 */
async function vectorizeContent(markdownContent, outputPath, options = {}) {
  try {
    const vectorizer = new TextVectorizer(options);
    
    // 对大型文本进行向量化
    const vectorData = vectorizer.vectorizeLargeText(markdownContent);
    
    // 保存向量化结果
    if (outputPath) {
      await vectorizer.saveVectorData(vectorData, outputPath);
    }
    
    return vectorData;
  } catch (error) {
    throw new Error(`向量化内容失败: ${error.message}`);
  }
}

module.exports = {
  TextVectorizer,
  vectorizeContent
};