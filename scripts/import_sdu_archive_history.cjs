/**
 * 将 SDU_Archive 前端中已审核的校史时间线导出为本项目的 JSON 知识库。
 *
 * 用法：
 * node scripts/import_sdu_archive_history.cjs <源 history.ts> <目标 json>
 */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const [input, output] = process.argv.slice(2);

if (!input || !output) {
  throw new Error('请提供源 history.ts 路径和目标 JSON 路径。');
}

let source = fs.readFileSync(input, 'utf8');
source = source
  .replace(/^import type .*?;\s*$/gm, '')
  .replace(/export const (\w+): \w+ =/g, 'const $1 =')
  .replace(/const (\w+): HistorySource =/g, 'const $1 =')
  .replace(/export const historyPeriods: HistoryPeriod\[\] =/, 'globalThis.historyPeriods =');

const context = {};
vm.createContext(context);
vm.runInContext(source, context, { filename: input });

if (!Array.isArray(context.historyPeriods)) {
  throw new Error('未能从源文件读取 historyPeriods。');
}

fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, `${JSON.stringify(context.historyPeriods, null, 2)}\n`, 'utf8');
console.log(`已导出 ${context.historyPeriods.length} 个时期到 ${output}`);
