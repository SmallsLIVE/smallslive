var gulp        = require('gulp');
var browserSync = require('browser-sync');
var sass        = require('gulp-sass');
var changed     = require('gulp-changed');
var sourcemaps  = require('gulp-sourcemaps');


// browser-sync task for starting the server.
gulp.task('browser-sync', function() {
    browserSync({
      proxy: process.env.PROXY || "127.0.0.1:8000",
      watchOptions: {
        reloadDelay: 300,
        reloadDebounce: 500
      },
      open: false,
      notify: {
        styles: {
          top: 'auto',
          bottom: '0',
          margin: '0px',
          padding: '5px',
          position: 'fixed',
          fontSize: '10px',
          zIndex: '9999',
          borderRadius: '5px 0px 0px',
          color: 'white',
          textAlign: 'center',
          display: 'block',
          backgroundColor: 'rgba(60, 197, 31, 0.498039)'
        }
      }
    });
});

// Sass task, will run when any SCSS files change & BrowserSync
// will auto-update browsers
gulp.task('sass', function () {
    return gulp.src('smallslive/static/sass/**/*.scss')
        .pipe(changed('smallslive/static/css'))
        .pipe(sourcemaps.init())
        .pipe(sass({errLogToConsole: true}))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest('smallslive/static/css'))
        .pipe(browserSync.reload({stream:true}));
});

// Reload all Browsers
gulp.task('bs-reload', function () {
    browserSync.reload();
});

// Default task to be run with `gulp`
gulp.task('default', ['browser-sync', 'sass'], function () {
    gulp.watch("smallslive/templates/**/*.html", ['bs-reload']);
    gulp.watch("smallslive/static/js/**/*.js", ['bs-reload']);
    gulp.watch("smallslive/static/sass/**/*.scss", ['sass']);
});
