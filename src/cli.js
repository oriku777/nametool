#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { Command, Option } from 'commander';
import dotenv from 'dotenv';
import { marked } from 'marked';
import { WpClient } from './wp-client.js';
import { WpBrowserClient } from './wp-browser-client.js';

dotenv.config();

function collect(value, previous) {
  return previous.concat([value]);
}

function loadClient() {
  return new WpClient({
    baseUrl: process.env.WP_URL,
    username: process.env.WP_USERNAME,
    appPassword: process.env.WP_APP_PASSWORD,
  });
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString('utf8');
}

function toHtml(raw, format) {
  if (format === 'html') return raw;
  // markdown (default): convert to HTML so it renders correctly in the block editor
  return marked.parse(raw);
}

async function resolveContent(opts) {
  const sources = [opts.content, opts.contentFile].filter(Boolean);
  if (sources.length > 1) {
    throw new Error('--content と --content-file は同時に指定できません。');
  }
  if (opts.content) return opts.content;
  if (opts.contentFile) return readFile(opts.contentFile, 'utf8');
  if (!process.stdin.isTTY) return readStdin();
  throw new Error('本文が指定されていません。--content, --content-file、または標準入力で渡してください。');
}

const program = new Command();

program
  .name('wp-post')
  .description('WordPress (REST API) へ記事を投稿するCLI');

program
  .command('whoami')
  .description('WordPressへの接続確認（認証が通るか確認します）')
  .action(async () => {
    const client = loadClient();
    const me = await client.getMe();
    console.log(`接続成功: ${me.name} (id=${me.id}, roles=${(me.roles || []).join(',')})`);
  });

program
  .command('post')
  .description('記事を投稿します（デフォルトは下書き保存）')
  .requiredOption('--title <title>', '記事タイトル')
  .option('--content <text>', '本文（Markdown）。--content-file や標準入力と併用不可')
  .option('--content-file <path>', '本文が書かれたファイルのパス')
  .addOption(new Option('--format <format>', '本文の形式').choices(['markdown', 'html']).default('markdown'))
  .addOption(
    new Option('--status <status>', '投稿ステータス')
      .choices(['draft', 'publish', 'pending'])
      .default('draft')
  )
  .option('--category <name>', 'カテゴリー名（複数指定可）', collect, [])
  .option('--tag <name>', 'タグ名（複数指定可）', collect, [])
  .option('--featured-image <path>', 'アイキャッチ画像のファイルパス')
  .option('--excerpt <text>', '抜粋')
  .option('--date <iso8601>', '公開日時（例: 2026-08-10T09:00:00）。未指定なら投稿と同時に公開/保存')
  .option('--yes', 'status=publish のときに確認なしで即時公開する', false)
  .action(async (opts) => {
    if (opts.status === 'publish' && !opts.yes) {
      console.error(
        '公開(publish)を指定しましたが --yes が付いていません。\n' +
          '内容を確認せずに一般公開すると事実誤り（募集人員・内申点など）のリスクがあるため、\n' +
          '安全のため一度 --status draft で下書き保存し、管理画面で確認してから公開するか、\n' +
          '確認済みなら --yes を付けて再実行してください。'
      );
      process.exitCode = 1;
      return;
    }

    let raw;
    try {
      raw = await resolveContent(opts);
    } catch (err) {
      console.error(err.message);
      process.exitCode = 1;
      return;
    }

    const content = toHtml(raw, opts.format);
    const client = loadClient();

    const categoryIds = opts.category.length ? await client.getOrCreateCategoryIds(opts.category) : undefined;
    const tagIds = opts.tag.length ? await client.getOrCreateTagIds(opts.tag) : undefined;

    let featuredMediaId;
    if (opts.featuredImage) {
      const media = await client.uploadMedia(path.resolve(opts.featuredImage));
      featuredMediaId = media.id;
    }

    const post = await client.createPost({
      title: opts.title,
      content,
      status: opts.status,
      excerpt: opts.excerpt,
      categoryIds,
      tagIds,
      featuredMediaId,
      date: opts.date,
    });

    console.log(`投稿完了: [${post.status}] ${post.title.rendered || opts.title}`);
    console.log(`編集画面: ${process.env.WP_URL}/wp-admin/post.php?post=${post.id}&action=edit`);
    if (post.status === 'publish') {
      console.log(`公開URL: ${post.link}`);
    }
  });

program
  .command('post-browser')
  .description(
    '記事を投稿します（ブラウザ自動操作版・実験的）。REST APIが使えない場合の代替手段です。カテゴリ/タグ/アイキャッチ画像には未対応です。'
  )
  .requiredOption('--title <title>', '記事タイトル')
  .option('--content <text>', '本文（Markdown）。--content-file や標準入力と併用不可')
  .option('--content-file <path>', '本文が書かれたファイルのパス')
  .addOption(new Option('--format <format>', '本文の形式').choices(['markdown', 'html']).default('markdown'))
  .addOption(
    new Option('--status <status>', '投稿ステータス').choices(['draft', 'publish']).default('draft')
  )
  .option('--yes', 'status=publish のときに確認なしで即時公開する', false)
  .option('--headed', 'ブラウザ画面を表示して実行する（デバッグ用）', false)
  .action(async (opts) => {
    if (opts.status === 'publish' && !opts.yes) {
      console.error(
        '公開(publish)を指定しましたが --yes が付いていません。\n' +
          '内容を確認せずに一般公開すると事実誤り（募集人員・内申点など）のリスクがあるため、\n' +
          '安全のため一度 --status draft で下書き保存し、管理画面で確認してから公開するか、\n' +
          '確認済みなら --yes を付けて再実行してください。'
      );
      process.exitCode = 1;
      return;
    }

    let raw;
    try {
      raw = await resolveContent(opts);
    } catch (err) {
      console.error(err.message);
      process.exitCode = 1;
      return;
    }

    const content = toHtml(raw, opts.format);

    const client = new WpBrowserClient({
      baseUrl: process.env.WP_URL,
      username: process.env.WP_USERNAME,
      password: process.env.WP_PASSWORD,
      headless: !opts.headed,
    });

    const result = await client.createPost({ title: opts.title, content, status: opts.status });
    console.log(`投稿完了 [${result.status}]。編集画面: ${result.url}`);
  });

program.parseAsync(process.argv).catch((err) => {
  console.error(err.message || err);
  process.exitCode = 1;
});
