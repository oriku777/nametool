import { readFile } from 'node:fs/promises';
import path from 'node:path';

function authHeader(username, appPassword) {
  const token = Buffer.from(`${username}:${appPassword}`).toString('base64');
  return `Basic ${token}`;
}

export class WpClient {
  constructor({ baseUrl, username, appPassword }) {
    if (!baseUrl || !username || !appPassword) {
      throw new Error('WP_URL / WP_USERNAME / WP_APP_PASSWORD が設定されていません（.env を確認してください）');
    }
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.apiRoot = `${this.baseUrl}/wp-json/wp/v2`;
    this.authHeader = authHeader(username, appPassword.replace(/\s+/g, ''));
  }

  async #request(pathname, { method = 'GET', body, headers = {} } = {}) {
    const res = await fetch(`${this.apiRoot}${pathname}`, {
      method,
      headers: {
        Authorization: this.authHeader,
        ...headers,
      },
      body,
    });

    const text = await res.text();
    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }

    if (!res.ok) {
      const message = data?.message || res.statusText;
      const err = new Error(`WordPress API エラー (${res.status}): ${message}`);
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  }

  async getMe() {
    return this.#request('/users/me?context=edit');
  }

  async findCategoryByName(name) {
    const results = await this.#request(`/categories?search=${encodeURIComponent(name)}&per_page=100`);
    return results.find((c) => c.name === name) ?? null;
  }

  async getOrCreateCategory(name) {
    const existing = await this.findCategoryByName(name);
    if (existing) return existing.id;
    const created = await this.#request('/categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    return created.id;
  }

  async findTagByName(name) {
    const results = await this.#request(`/tags?search=${encodeURIComponent(name)}&per_page=100`);
    return results.find((t) => t.name === name) ?? null;
  }

  async getOrCreateTag(name) {
    const existing = await this.findTagByName(name);
    if (existing) return existing.id;
    const created = await this.#request('/tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    return created.id;
  }

  async getOrCreateCategoryIds(names = []) {
    const ids = [];
    for (const name of names) {
      ids.push(await this.getOrCreateCategory(name));
    }
    return ids;
  }

  async getOrCreateTagIds(names = []) {
    const ids = [];
    for (const name of names) {
      ids.push(await this.getOrCreateTag(name));
    }
    return ids;
  }

  async uploadMedia(filePath) {
    const fileBuffer = await readFile(filePath);
    const filename = path.basename(filePath);
    const blob = new Blob([fileBuffer]);

    const form = new FormData();
    form.append('file', blob, filename);

    return this.#request('/media', {
      method: 'POST',
      body: form,
    });
  }

  async createPost({ title, content, status = 'draft', excerpt, categoryIds, tagIds, featuredMediaId, date }) {
    const body = {
      title,
      content,
      status,
    };
    if (excerpt) body.excerpt = excerpt;
    if (categoryIds?.length) body.categories = categoryIds;
    if (tagIds?.length) body.tags = tagIds;
    if (featuredMediaId) body.featured_media = featuredMediaId;
    if (date) body.date = date;

    return this.#request('/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  }
}
