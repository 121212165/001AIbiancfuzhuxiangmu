#!/usr/bin/env node

const { program } = require('commander');
const path = require('path');
const fs = require('fs-extra');
const cliProgress = require('cli-progress');
const chalk = require('chalk');
const { convertPdfToMarkdown } = require('./converter');
const { findPdfFiles, ensureOutputDirectory, getOutputFilePath } = require('./utils');

// 设置命令行参数
program
  .name('pdf-to-markdown')
  .description('将PDF文件转换为Markdown格式')
  .version('1.0.0')
  .option('-i, --input <path>', '输入PDF文件或包含PDF文件的目录路径')
  .option('-o, --output <path>', '输出Markdown文件或目录路径')
  .option('-r, --recursive', '递归处理子目录中的PDF文件', false)
  .option('-v, --vectorize', '生成文本向量表示', false)
  .option('--vector-output <path>', '向量化数据输出路径（可选）')
  .parse(process.argv);

const options = program.opts();

// 主函数
async function main() {
  try {
    if (!options.input) {
      console.error(chalk.red('错误: 必须指定输入路径'));
      program.help();
      return;
    }

    const inputPath = path.resolve(options.input);
    let outputPath = options.output ? path.resolve(options.output) : path.dirname(inputPath);

    // 检查输入路径是否存在
    if (!fs.existsSync(inputPath)) {
      console.error(chalk.red(`错误: 输入路径 "${inputPath}" 不存在`));
      return;
    }

    // 确定是单个文件还是目录
    const isDirectory = fs.statSync(inputPath).isDirectory();
    
    // 如果是单个文件
    if (!isDirectory) {
      if (!inputPath.toLowerCase().endsWith('.pdf')) {
        console.error(chalk.red('错误: 输入文件必须是PDF格式'));
        return;
      }

      // 如果输出路径是目录，确保它存在
      if (options.output && !outputPath.toLowerCase().endsWith('.md')) {
        await ensureOutputDirectory(outputPath);
        outputPath = getOutputFilePath(inputPath, outputPath);
      } else if (!options.output) {
        // 默认输出到同一目录，但扩展名改为.md
        outputPath = path.join(path.dirname(inputPath), `${path.basename(inputPath, '.pdf')}.md`);
      }

      console.log(chalk.blue(`开始转换: ${inputPath} -> ${outputPath}`));
      
      // 准备转换选项
      const conversionOptions = {
        vectorize: options.vectorize,
        vectorOutputPath: options.vectorOutput
      };
      
      const result = await convertPdfToMarkdown(inputPath, outputPath, conversionOptions);
      
      console.log(chalk.green(`✓ 转换完成: ${result.outputPath} (${result.pageCount} 页)`));
      
      // 如果启用了向量化，显示向量化结果
      if (options.vectorize && result.vectorOutputPath) {
        console.log(chalk.green(`✓ 向量化完成: ${result.vectorOutputPath}`));
        console.log(chalk.blue(`  - 提取了 ${result.vectorData.keywords.length} 个关键词`));
        console.log(chalk.blue(`  - 识别了 ${result.vectorData.entities.length} 个命名实体`));
      }
    } 
    // 如果是目录
    else {
      // 确保输出目录存在
      await ensureOutputDirectory(outputPath);
      
      // 查找所有PDF文件
      const pdfFiles = await findPdfFiles(inputPath);
      
      if (pdfFiles.length === 0) {
        console.log(chalk.yellow('警告: 未找到PDF文件'));
        return;
      }
      
      console.log(chalk.blue(`找到 ${pdfFiles.length} 个PDF文件`));
      
      // 创建进度条
      const progressBar = new cliProgress.SingleBar({
        format: '转换进度 |' + chalk.cyan('{bar}') + '| {percentage}% || {value}/{total} 文件',
        barCompleteChar: '\u2588',
        barIncompleteChar: '\u2591',
        hideCursor: true
      });
      
      progressBar.start(pdfFiles.length, 0);
      
      // 转换所有PDF文件
      const results = [];
      for (let i = 0; i < pdfFiles.length; i++) {
        const pdfPath = pdfFiles[i];
        const mdPath = getOutputFilePath(pdfPath, outputPath);
        
        try {
          // 准备转换选项
          const conversionOptions = {
            vectorize: options.vectorize,
            vectorOutputPath: options.vectorOutput ? 
              path.join(options.vectorOutput, `${path.basename(pdfPath, '.pdf')}.vector.json`) : 
              undefined
          };
          
          const result = await convertPdfToMarkdown(pdfPath, mdPath, conversionOptions);
          results.push({ ...result, inputPath: pdfPath, success: true });
        } catch (error) {
          results.push({ inputPath: pdfPath, outputPath: mdPath, success: false, error: error.message });
        }
        
        progressBar.update(i + 1);
      }
      
      progressBar.stop();
      
      // 显示结果摘要
      const successCount = results.filter(r => r.success).length;
      const failCount = results.length - successCount;
      
      console.log(chalk.green(`\n✓ 成功转换: ${successCount} 个文件`));
      
      if (failCount > 0) {
        console.log(chalk.red(`✗ 转换失败: ${failCount} 个文件`));
        results.filter(r => !r.success).forEach(result => {
          console.log(chalk.red(`  - ${result.inputPath}: ${result.error}`));
        });
      }
    }
  } catch (error) {
    console.error(chalk.red(`错误: ${error.message}`));
    process.exit(1);
  }
}

// 运行主函数
main();