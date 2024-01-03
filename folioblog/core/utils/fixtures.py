from collections import OrderedDict

fixtures_map = OrderedDict(
    [
        # Core
        ("locales", "wagtailcore.Locale"),
        ("pages", "wagtailcore.Page"),
        ("sites", "wagtailcore.Site"),
        ("collections", "wagtailcore.Collection"),
        ("photographers", "core.Photographer"),
        ("images", "core.FolioImage"),
        ("renditions", "core.FolioRendition"),
        ("settings", "core.FolioBlogSettings"),
        ("tags", "taggit.Tag"),
        ("taggeditems", "taggit.TaggedItem"),
        ("embeds", "wagtailembeds.Embed"),
        # Home pages
        ("homepage", "home.HomePage"),
        # Blog pages
        ("blogcategories", "blog.BlogCategory"),
        ("blogindex", "blog.BlogIndexPage"),
        ("blogpages", "blog.BlogPage"),
        ("blogtags", "blog.BlogTag"),
        ("blogpagetags", "blog.BlogPageTag"),
        ("blogpromote", "blog.BlogPromote"),
        ("blogpromotelink", "blog.BlogPromoteLink"),
        # Video pages
        ("videocategories", "video.VideoCategory"),
        ("videoindex", "video.VideoIndexPage"),
        ("videopages", "video.VideoPage"),
        ("videotags", "video.VideoTag"),
        ("videopagetags", "video.VideoPageTag"),
        ("videopromote", "video.VideoPromote"),
        ("videopromotelink", "video.VideoPromoteLink"),
        # Basic pages
        ("basicpages", "core.BasicPage"),
        # Other page types
        ("gallerypage", "gallery.GalleryPage"),
        ("searchindex", "search.SearchIndexPage"),
        # Page relationships
        ("basicpagerelatedlinks", "core.BasicPageRelatedLink"),
        ("blogpagerelatedlinks", "blog.BlogPageRelatedLink"),
        ("videopagerelatedlinks", "video.VideoPageRelatedLink"),
        # Remaining stuff
        ("menu", "core.Menu"),
        ("menulink", "core.MenuLink"),
        ("referenceindex", "wagtailcore.ReferenceIndex"),
    ]
)
