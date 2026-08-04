import { chromium } from 'playwright';

// Gutenberg (WordPress標準ブロックエディタ) の画面をブラウザ操作で埋める実装。
// REST API 版と違い、管理画面のマークアップに依存するため、テーマやWordPressの
// バージョンアップでセレクタが変わると動かなくなる可能性がある点に注意。
export class WpBrowserClient {
  constructor({ baseUrl, username, password, headless = true }) {
    if (!baseUrl || !username || !password) {
      throw new Error('WP_URL / WP_USERNAME / WP_PASSWORD が設定されていません（.env を確認してください）');
    }
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.username = username;
    this.password = password;
    this.headless = headless;
  }

  async #login(page) {
    await page.goto(`${this.baseUrl}/wp-login.php`, { waitUntil: 'domcontentloaded' });
    await page.fill('#user_login', this.username);
    await page.fill('#user_pass', this.password);
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
      page.click('#wp-submit'),
    ]);
    if (page.url().includes('wp-login.php')) {
      throw new Error('ログインに失敗しました。WP_USERNAME / WP_PASSWORD を確認してください。');
    }
  }

  async #dismissWelcomeGuide(page) {
    const closeButtons = page.locator(
      '.edit-post-welcome-guide button[aria-label="閉じる"], .components-modal__header button[aria-label="Close"], .components-modal__header button[aria-label="閉じる"]'
    );
    if (await closeButtons.first().isVisible({ timeout: 3000 }).catch(() => false)) {
      await closeButtons.first().click().catch(() => {});
    }
  }

  async createPost({ title, content, status = 'draft' }) {
    const launchOptions = { headless: this.headless };
    if (process.env.PLAYWRIGHT_CHROMIUM_PATH) {
      launchOptions.executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH;
    }
    const browser = await chromium.launch(launchOptions);
    try {
      const page = await browser.newPage();
      await this.#login(page);

      await page.goto(`${this.baseUrl}/wp-admin/post-new.php`, { waitUntil: 'domcontentloaded' });
      await this.#dismissWelcomeGuide(page);

      const titleField = page.locator('.editor-post-title__input, [aria-label="タイトルを追加"]').first();
      await titleField.waitFor({ state: 'visible', timeout: 30000 });
      await titleField.click();
      await titleField.fill(title);

      const htmlBlockTextarea = page.locator('.wp-block-html textarea, textarea.block-library-html__textarea').first();
      if (await htmlBlockTextarea.count()) {
        await htmlBlockTextarea.click();
        await htmlBlockTextarea.fill(content);
      } else {
        // 「カスタムHTML」ブロックが見つからない場合のフォールバック:
        // 本文キャンバスをクリックしてそのままテキストを流し込む（書式は失われる）
        const canvas = page.locator('.block-editor-writing-flow, .is-root-container').first();
        await canvas.click();
        await page.keyboard.type(content);
      }

      if (status === 'publish') {
        await page.getByRole('button', { name: '公開', exact: true }).first().click();
        const confirmButton = page.locator(
          '.editor-post-publish-panel__header-publish-button button, .editor-post-publish-button'
        );
        await confirmButton.first().click({ timeout: 15000 }).catch(() => {});
        await page.waitForSelector('text=投稿を公開しました', { timeout: 20000 }).catch(() => {});
      } else {
        await page.getByRole('button', { name: '下書き保存', exact: true }).first().click();
        await page.waitForTimeout(2000);
      }

      return { url: page.url(), status };
    } finally {
      await browser.close();
    }
  }
}
