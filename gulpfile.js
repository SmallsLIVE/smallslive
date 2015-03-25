var gulp        = require('gulp');
var browserSync = require('browser-sync');
var sass        = require('gulp-sass');
var watch       = require('gulp-watch');
var sourcemaps  = require('gulp-sourcemaps');


// browser-sync task for starting the server.
gulp.task('browser-sync', function() {
    browserSync({
        proxy: "127.0.0.1:8000"
    });
});

// Sass task, will run when any SCSS files change & BrowserSync
// will auto-update browsers
gulp.task('sass', function () {
    return gulp.src('smallslive/static/sass/**/*.scss')
        .pipe(watch('smallslive/static/sass/**/*.scss'), {verbose: true, name: 'SASS'})
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
});
