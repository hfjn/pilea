import os
from pathlib import Path

import yaml
from click import make_pass_decorator

import pendulum

from pilea.post import Post

DEFAULT_PATH = Path("input")
TEMPLATE_FOLDER = "templates"
STATIC_FOLDER = "css"
OUTPUT_FOLDER = "site"


class State(object):
    def __init__(self):
        self.pwd: Path = Path(os.getcwd())

        self._cfg = yaml.safe_load((DEFAULT_PATH / "config.yaml").read_text())
        self.host_name = self._cfg["host_name"]
        self.posts = self.gather_posts()
        self.pages = self.gather_pages()

    def gather_posts(self):
        posts = [Post(self, file) for file in self.posts_folder.glob("**/*.md")]
        posts = [post for post in posts if not post.draft]
        posts.sort(key=lambda x: x.date, reverse=True)
        return posts

    def gather_pages(self):
        pages = [Post(self, file) for file in self.pages_folder.glob("**/*.md")]
        return pages

    @property
    def title(self):
        return self._cfg["title"]

    @property
    def subtitle(self):
        return self._cfg["subtitle"]

    @property
    def url(self):
        return self._cfg["url"]

    @property
    def num_posts(self):
        return len(self.posts)
    
    @property
    def language(self):
        return self._cfg["language"]

    @property
    def input_folder(self):
        return self.pwd / "input"

    @property
    def content_folder(self):
        return self.input_folder / "content"

    @property
    def pages_folder(self):
        return self.content_folder / "pages"

    @property
    def posts_folder(self):
        return self.content_folder / "posts"

    @property
    def static_folder(self):
        return self.input_folder / "static"

    @property
    def original_css(self):
        return self.static_folder / "style.css"

    @property
    def author_age(self):
        return pendulum.parse(self._cfg["birthday"]).diff(pendulum.now()).years

    @property
    def css(self):
        return "/static/style.css"

    @property
    def output_folder(self):
        return self.pwd / "site"

    @property
    def atom_url(self):
        return "/atom.xml"

    @property
    def rss_path(self):
        return self.output_folder / "rss.xml"

    @property
    def rss_url(self):
        return "/rss.xml"

    @property
    def atom_path(self):
        return self.output_folder / "atom.xml"

    @property
    def template_folder(self):
        return self.pwd / DEFAULT_PATH / TEMPLATE_FOLDER

    def build_output_file_name(self, post: Post) -> Path:
        content_path = self.extract_relative_file_path(post.file)

        return self.output_folder / content_path.parent / f"{post.id}.html"

    def extract_relative_file_path(self, file):
        content_path = Path(file.relative_to(self.content_folder))
        return content_path


pass_state = make_pass_decorator(State, ensure=True)
