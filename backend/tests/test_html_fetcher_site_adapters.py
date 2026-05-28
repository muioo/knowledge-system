import os
import unittest
from unittest.mock import patch

from backend.utils.html_fetcher import clean_html


class HtmlFetcherSiteAdaptersTest(unittest.TestCase):
    """验证特殊站点的 HTML 提取适配。"""

    def test_wechat_article_uses_js_content_and_lazy_images(self):
        """微信公众号文章应从 js_content 提取正文并恢复懒加载图片。"""
        html = """
        <html><body>
          <h1 id="activity-name">微信标题</h1>
          <a id="js_name">公众号</a>
          <div id="js_content">
            <p>第一段正文</p>
            <img data-src="https://img.example/a.jpg" />
          </div>
        </body></html>
        """

        content, title = clean_html(html, "https://mp.weixin.qq.com/s/demo")

        self.assertEqual(title, "微信标题")
        self.assertIn("第一段正文", content)
        self.assertIn('src="https://img.example/a.jpg"', content)

    def test_zhihu_headers_use_cookie_from_environment(self):
        """知乎请求头应支持从环境变量读取 Cookie。"""
        from backend.utils.html_fetcher import build_request_headers

        with patch.dict(os.environ, {"ZHIHU_COOKIE": "z_c0=test-cookie"}):
            headers = build_request_headers("https://zhuanlan.zhihu.com/p/1")

        self.assertEqual(headers["Cookie"], "z_c0=test-cookie")
        self.assertIn("www.zhihu.com", headers["Referer"])


if __name__ == "__main__":
    unittest.main()
