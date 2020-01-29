import re
import shutil
from pathlib import Path

import click
import jinja2
import markdown
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator

from pilea.resources.photo import Photo
from pilea.resources.post import Post
from pilea.state import State


class BuildController:
    def __init__(self, state: State):
        self.state = state
        self.template_loader = jinja2.FileSystemLoader(searchpath=str(self.state.template_folder))
        self.template_env = jinja2.Environment(loader=self.template_loader)

    def build_all(self):
        self.process_posts()
        self.process_pages()
        self.process_photos()
        self.build_index("index")
        self.build_index("archive")
        self.build_feed()
        self.copy_static()
        self.minify_css()

    def build_css(self):
        self.copy_static()
        self.minify_css()

    def _configure_feed_generator(self):
        feed_generator = FeedGenerator()
        feed_generator.id("123")
        feed_generator.title(self.state.title)
        feed_generator.description(self.state.subtitle)
        feed_generator.language(self.state.language)
        feed_generator.link(href=self.state.url, rel="self")
        return feed_generator

    def build_feed(self):
        feed_gen = self._configure_feed_generator()
        for post in self.state.posts:
            post_url = self.state.generate_url(post)
            entry = FeedEntry()
            entry.title(post.title)
            entry.description(post.stub)
            entry.content(post.content)
            entry.guid(post_url)
            entry.link(href=post_url, rel="self")
            feed_gen.add_entry(entry)
        feed_gen.atom_file(str(self.state.atom_path))
        feed_gen.rss_file(str(self.state.rss_path))

    def process_photos(self):
        for photo in self.state.photos:
            self.process_photo(photo)

    def process_posts(self):
        for post in self.state.posts:
            self.process_markdown(post)

    def process_pages(self):
        for page in self.state.pages:
            self.process_markdown(page)

    def process_photo(self, photo: Photo):
        click.echo(f"Compiling {photo.file}")
        photo.scale()
        photo.save(path=self.state.output_folder)

    def process_markdown(self, post: Post):
        click.echo(f"Compiling {post.title}")
        post.content = markdown.markdown(
            post.content, output_format="html5", extensions=["codehilite", "fenced_code", "pymdownx.tilde"]
        )
        post.stub = markdown.markdown(
            post.stub, output_format="html5", extensions=["codehilite", "fenced_code", "pymdownx.tilde"]
        )
        doc = self._render_template(post.template, post=post, state=self.state)
        output_file: Path = self.state.build_output_file_name(post)
        self._ensure_parent_folder_exists(output_file)
        output_file.write_text(doc)

    def _ensure_parent_folder_exists(self, output_file):
        if not output_file.parent.exists():
            output_file.parent.mkdir(parents=True)

    def _render_template(self, template, **kwargs) -> str:
        template = self.template_env.get_template(f"{template}.html")
        return template.render(**kwargs)

    def build_index(self, name: str):
        content = self._render_template(name, state=self.state)
        output_file: Path = self.state.output_folder / f"{name}.html"
        self._ensure_parent_folder_exists(output_file)
        output_file.write_text(content)

    def sync(self, root: Path, target_root: Path):
        for file in root.glob("**/*"):
            if file.is_dir():
                continue
            file = Path(file)
            print(Path(target_root / file.relative_to(root)))
            target = Path(target_root / file.relative_to(root))

            if self._need_to_copy(file, target):
                if not target.parent.exists():
                    target.mkdir(parents=True)
                shutil.copy(file, target)
                print(f"Copy {file}")

    def _need_to_copy(self, source: Path, target: Path):
        if not target.exists():
            return True

        return (source.stat().st_mtime - target.stat().st_mtime) > 1

    def copy_static(self):
        self.sync(self.state.static_folder, self.state.output_folder / "static")

    def minify_css(self):
        minified_css = ""
        for css_file in self.state.static_folder.glob("*.css"):
            css = css_file.read_text()
            css = re.sub(r"\s*/\*\s*\*/", "$$HACK1$$", css)
            css = re.sub(r"/\*[\s\S]*?\*/", "", css)
            css = css.replace("$$HACK1$$", "/**/")
            css = re.sub(r'url\((["\'])([^)]*)\1\)', r"url(\2)", css)
            css = re.sub(r"\s+", " ", css)
            css = re.sub(r"#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)", r"#\1\2\3\4", css)
            css = re.sub(r":\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;", r":\1;", css)
            for rule in re.findall(r"([^{]+){([^}]*)}", css):
                selectors = [
                    re.sub(r"(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])", r"", selector.strip())
                    for selector in rule[0].split(",")
                ]
                properties = {}
                porder = []
                for prop in re.findall("(.*?):(.*?)(;|$)", rule[1]):
                    key = prop[0].strip().lower()
                    if key not in porder:
                        porder.append(key)
                    properties[key] = prop[1].strip()
                if properties:
                    minified_css += "%s{%s}" % (
                        ",".join(selectors),
                        "".join(["%s:%s;" % (key, properties[key]) for key in porder])[:-1],
                    )

        output_file: Path = self.state.output_folder / "static" / "style.css"
        self._ensure_parent_folder_exists(output_file)
        output_file.write_text(minified_css)
