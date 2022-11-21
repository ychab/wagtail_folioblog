#!/bin/bash

PROJECT_PATH=$(pwd ${BASH_SOURCE[0]}/../)

BOOTSTRAP_PATH=${PROJECT_PATH}/node_modules/bootstrap
THEME_FOLIO_PATH=${PROJECT_PATH}/node_modules/startbootstrap-agency
THEME_BLOG_PATH=${PROJECT_PATH}/node_modules/startbootstrap-clean-blog

FONTAWESOME_PATH=${PROJECT_PATH}/node_modules/@fortawesome/fontawesome-free
COOKIES_BANNER_PATH=${PROJECT_PATH}/node_modules/cookies-eu-banner
PACKERY_PATH=${PROJECT_PATH}/node_modules/packery
DRAGGABILLY_PATH=${PROJECT_PATH}/node_modules/draggabilly
FLICKITY_PATH=${PROJECT_PATH}/node_modules/flickity
INFINITE_SCROLL_PATH=${PROJECT_PATH}/node_modules/infinite-scroll
TAGIFY_PATH=${PROJECT_PATH}/node_modules/@yaireo/tagify
AUTOCOMPLETE_PATH=${PROJECT_PATH}/node_modules/@tarekraafat/autocomplete.js
GLIGHTBOX_PATH=${PROJECT_PATH}/node_modules/glightbox

prepare() {
    echo ">>> Override SCSS variables"
    cp $PROJECT_PATH/dist/build/scss/variables/_colors.scss $THEME_FOLIO_PATH/src/scss/variables/
    cp $PROJECT_PATH/dist/build/scss/components/_navbar.scss $THEME_FOLIO_PATH/src/scss/components/
}

build_folio() {
  echo ">>> Build Agency Theme"
  cd $THEME_FOLIO_PATH && npm install && npm run build
  rm -Rf $PROJECT_PATH/folioblog/static/agency
  mkdir $PROJECT_PATH/folioblog/static/agency
  cp -Ra $THEME_FOLIO_PATH/dist/css $PROJECT_PATH/folioblog/static/agency/
  cp -Ra $THEME_FOLIO_PATH/dist/js $PROJECT_PATH/folioblog/static/agency/
  cp -Ra $THEME_FOLIO_PATH/dist/assets $PROJECT_PATH/folioblog/static/agency/
}

build_blog() {
  echo ">>> Build CleanBlog Theme"
  cd $THEME_BLOG_PATH && npm install && npm run build
  rm -Rf $PROJECT_PATH/folioblog/static/cleanblog
  mkdir $PROJECT_PATH/folioblog/static/cleanblog
  cp -Ra $THEME_BLOG_PATH/dist/css $PROJECT_PATH/folioblog/static/cleanblog/
  cp -Ra $THEME_BLOG_PATH/dist/js $PROJECT_PATH/folioblog/static/cleanblog/
}

build_third_party() {
  echo ">>> Copy bootstrap"
  rm -Rf $PROJECT_PATH/folioblog/static/bootstrap
  mkdir -p $PROJECT_PATH/folioblog/static/bootstrap/js
  cp $BOOTSTRAP_PATH/dist/js/bootstrap.bundle.js $PROJECT_PATH/folioblog/static/bootstrap/js/
  # Remove source map not used for dev
  sed -i -E 's/\/\/# sourceMappingURL=bootstrap.bundle.js.map//g' $PROJECT_PATH/folioblog/static/bootstrap/js/bootstrap.bundle.js

  echo ">>> Copy fontawesome"
  rm -Rf $PROJECT_PATH/folioblog/static/fontawesome
  mkdir -p $PROJECT_PATH/folioblog/static/fontawesome/js/
  cp $FONTAWESOME_PATH/js/all.js $PROJECT_PATH/folioblog/static/fontawesome/js/

  echo ">>> Copy infinite-scroll"
  rm -Rf $PROJECT_PATH/folioblog/static/infinite-scroll
  mkdir $PROJECT_PATH/folioblog/static/infinite-scroll/
  cp $INFINITE_SCROLL_PATH/dist/infinite-scroll.pkgd.js $PROJECT_PATH/folioblog/static/infinite-scroll/

  echo ">>> Copy tagify"
  rm -Rf $PROJECT_PATH/folioblog/static/tagify
  mkdir $PROJECT_PATH/folioblog/static/tagify/
  cp $TAGIFY_PATH/dist/{tagify.js,tagify.css} $PROJECT_PATH/folioblog/static/tagify/

  echo ">>> Copy autocomplete"
  rm -Rf $PROJECT_PATH/folioblog/static/autocomplete
  mkdir $PROJECT_PATH/folioblog/static/autocomplete
  cp $AUTOCOMPLETE_PATH/dist/autoComplete.js $PROJECT_PATH/folioblog/static/autocomplete/

  echo ">>> Copy packery"
  rm -Rf $PROJECT_PATH/folioblog/static/packery
  mkdir $PROJECT_PATH/folioblog/static/packery
  cp $PACKERY_PATH/dist/packery.pkgd.js $PROJECT_PATH/folioblog/static/packery/

  echo ">>> Copy flickity"
  rm -Rf $PROJECT_PATH/folioblog/static/flickity
  mkdir $PROJECT_PATH/folioblog/static/flickity
  cp $FLICKITY_PATH/dist/{flickity.pkgd.js,flickity.css} $PROJECT_PATH/folioblog/static/flickity/

  echo ">>> Copy draggabilly"
  rm -Rf $PROJECT_PATH/folioblog/static/draggabilly
  mkdir $PROJECT_PATH/folioblog/static/draggabilly/
  cp $DRAGGABILLY_PATH/dist/draggabilly.pkgd.js $PROJECT_PATH/folioblog/static/draggabilly/

  echo ">>> Copy cookies-eu-banner"
  rm -Rf $PROJECT_PATH/folioblog/static/cookies-eu-banner
  mkdir $PROJECT_PATH/folioblog/static/cookies-eu-banner/
  cp $COOKIES_BANNER_PATH/dist/cookies-eu-banner.js $PROJECT_PATH/folioblog/static/cookies-eu-banner/

  echo ">>> Copy glightbox"
  rm -Rf $PROJECT_PATH/folioblog/static/glightbox/
  mkdir $PROJECT_PATH/folioblog/static/glightbox/
  cp $GLIGHTBOX_PATH/dist/js/glightbox.js $PROJECT_PATH/folioblog/static/glightbox/
  cp $GLIGHTBOX_PATH/dist/css/glightbox.css $PROJECT_PATH/folioblog/static/glightbox/
}

prepare
build_folio
build_blog
build_third_party
