from faker.providers import BaseProvider


class Provider(BaseProvider):
    youtube_urls = [
        "https://www.youtube.com/watch?v=OeXFD1Aps1g",  # Reveeeeeenge
    ]

    def youtube_url(self):
        return self.generator.random.choice(self.youtube_urls)
