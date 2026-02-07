const fs = require('fs-extra');
const path = require('path');
const pdfParse = require('pdf-parse');
const TurndownService = require('turndown');
const cheerio = require('cheerio');
const { createChunks } = require('./utils');
const { vectorizeContent } = require('./vectorizer');

// 创建Turndown实例用于HTML到Markdown的转换
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
  emDelimiter: '*'
});

// 增强turndown以更好地处理PDF内容
turndownService.addRule('preserveIndent', {
  filter: ['pre', 'code'],
  replacement: function(content) {
    return '```\n' + content + '\n```';
  }
});

/**
 * 将PDF文件转换为Markdown
 * @param {string} pdfPath PDF文件路径
 * @param {string} outputPath 输出Markdown文件路径
 * @param {Object} options 转换选项
 * @param {boolean} options.vectorize 是否进行向量化
 * @param {string} options.vectorOutputPath 向量化输出路径
 * @returns {Promise<Object>} 转换结果
 */
async function convertPdfToMarkdown(pdfPath, outputPath, options = {}) {
  try {
    // 读取PDF文件
    const dataBuffer = await fs.readFile(pdfPath);
    
    // 解析PDF内容
    const pdfData = await pdfParse(dataBuffer);
    
    // 处理PDF文本内容
    const processedText = processPdfText(pdfData.text, options);
    
    // 将处理后的文本转换为Markdown
    const markdown = convertToMarkdown(processedText, options);
    
    // 写入输出文件
    await fs.writeFile(outputPath, markdown, 'utf8');
    
    // 结果对象
    const result = {
      pageCount: pdfData.numpages,
      outputPath
    };
    
    // 如果启用了向量化
    if (options.vectorize) {
      // 确定向量化输出路径
      const vectorOutputPath = options.vectorOutputPath || 
        outputPath.replace(/\.md$/, '.vector.json');
      
      // 执行向量化
      const vectorData = await vectorizeContent(markdown, vectorOutputPath);
      
      // 将向量化结果添加到返回对象
      result.vectorData = vectorData;
      result.vectorOutputPath = vectorOutputPath;
    }
    
    return result;
  } catch (error) {
    throw new Error(`转换PDF文件 ${pdfPath} 失败: ${error.message}`);
  }
}

/**
 * 处理PDF文本内容
 * @param {string} text PDF文本内容
 * @param {Object} options 处理选项
 * @returns {string} 处理后的文本
 */
function processPdfText(text, options = {}) {
  // 移除多余的空行
  let processedText = text.replace(/\n{3,}/g, '\n\n');
  
  // 处理标题（假设标题是单独的行，且通常较短）
  processedText = processedText.replace(/^(.{1,60})(?:\n)/gm, (match, p1) => {
    // 如果这行文本看起来像标题（不以标点符号结尾，且不太长）
    if (!/[.,:;]$/.test(p1.trim()) && p1.trim().length > 0 && p1.trim().length < 60) {
      return `# ${p1.trim()}\n\n`;
    }
    return match;
  });
  
  // 处理列表项
  processedText = processedText.replace(/^(\s*)[•·○◦-]\s+(.+)$/gm, (match, indent, content) => {
    return `${indent}- ${content}`;
  });
  
  // 处理数字列表
  processedText = processedText.replace(/^(\s*)(\d+)[.、]\s+(.+)$/gm, (match, indent, num, content) => {
    return `${indent}${num}. ${content}`;
  });
  
  return processedText;
}

/**
 * 将处理后的文本转换为Markdown
 * @param {string} text 处理后的文本
 * @param {Object} options 转换选项
 * @returns {string} Markdown文本
 */
function convertToMarkdown(text, options = {}) {
  // 创建一个简单的HTML结构
  const html = `<div>${text.replace(/\n/g, '<br>')}</div>`;
  
  // 使用cheerio解析HTML
  const $ = cheerio.load(html);
  
  // 处理段落
  $('div').contents().each(function() {
    if (this.type === 'text' || this.tagName === 'br') {
      const text = $(this).text().trim();
      if (text) {
        $(this).replaceWith(`<p>${text}</p>`);
      }
    }
  });
  
  // 获取处理后的HTML
  const processedHtml = $('div').html();
  
  // 使用turndown将HTML转换为Markdown
  return turndownService.turndown(processedHtml || '');
}

module.exports = {
  convertPdfToMarkdown
};