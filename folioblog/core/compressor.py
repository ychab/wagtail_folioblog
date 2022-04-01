from compressor.conf import settings
from compressor.filters import CompilerFilter


class UglifyJSFilter(CompilerFilter):
    command = "{binary} {args} --compress --mangle -o {outfile} {infile}"
    options = (
        ("binary", settings.FOLIOBLOG_COMPRESSOR_UGLIFY_BINARY),
        ("args", settings.FOLIOBLOG_COMPRESSOR_UGLIFY_ARGUMENTS),
    )
