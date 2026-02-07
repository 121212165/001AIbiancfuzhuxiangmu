const fs = require('fs-extra');
const path = require('path');
const glob = require('glob');

/**
 * 将大文本分割成更小的块以便处理
 * @param {string} text 要分割的文本
 * @param {number} chunkSize 每个块的最大大小
 * @returns {Array<string>} 文本块数组
 */
function createChunks(text, chunkSize = 100000) {
  const chunks = [];
  let i = 0;
  while (i < text.length) {
    chunks.push(text.slice(i, i + chunkSize));
    i += chunkSize;
  }
  return chunks;
}

/**
 * 查找指定目录下的所有PDF文件
 * @param {string} directory 要搜索的目录
 * @returns {Promise<Array<string>>} PDF文件路径数组
 */
function findPdfFiles(directory) {
  return new Promise((resolve, reject) => {
    glob(path.join(directory, '**/*.pdf'), (err, files) => {
      if (err) {
        reject(err);
      } else {
        resolve(files);
      }
    });
  });
}

/**
 * 确保输出目录存在
 * @param {string} outputDir 输出目录路径
 * @returns {Promise<void>}
 */
async function ensureOutputDirectory(outputDir) {
  await fs.ensureDir(outputDir);
}

/**
 * 生成输出文件路径
 * @param {string} pdfPath PDF文件路径
 * @param {string} outputDir 输出目录
 * @returns {string} Markdown文件路径
 */
function getOutputFilePath(pdfPath, outputDir) {
  const pdfFileName = path.basename(pdfPath, '.pdf');
  return path.join(outputDir, `${pdfFileName}.md`);
}

module.exports = {
  createChunks,
  findPdfFiles,
  ensureOutputDirectory,
  getOutputFilePath
};