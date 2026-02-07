const path = require('path');
const fs = require('fs-extra');
const { convertPdfToMarkdown } = require('./converter');

// 测试函数
async function testConversion() {
  try {
    console.log('开始测试PDF转Markdown功能...');
    
    // 创建测试目录
    const testDir = path.join(__dirname, '../test');
    await fs.ensureDir(testDir);
    
    // 检查是否有测试PDF文件
    const testPdfPath = path.join(testDir, 'test.pdf');
    if (!fs.existsSync(testPdfPath)) {
      console.log('未找到测试PDF文件。请将一个名为test.pdf的文件放在test目录中进行测试。');
      return;
    }
    
    // 设置输出路径
    const outputPath = path.join(testDir, 'test-output.md');
    
    console.log(`转换测试文件: ${testPdfPath} -> ${outputPath}`);
    
    // 执行转换
    const result = await convertPdfToMarkdown(testPdfPath, outputPath);
    
    console.log(`转换完成! 输出文件: ${result.outputPath}`);
    console.log(`页数: ${result.pageCount}`);
    
    // 显示转换后的部分内容
    const mdContent = await fs.readFile(outputPath, 'utf8');
    console.log('\n转换后的Markdown内容预览 (前500个字符):');
    console.log('-----------------------------------');
    console.log(mdContent.substring(0, 500) + '...');
    console.log('-----------------------------------');
    
    console.log('\n测试完成!');
  } catch (error) {
    console.error(`测试失败: ${error.message}`);
  }
}

// 运行测试
testConversion();