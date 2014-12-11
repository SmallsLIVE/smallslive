var gulp        = require('gulp');
var browserSync = require('browser-sync');
var sass        = require('gulp-sass');

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
        .pipe(sass())
        .pipe(gulp.dest('smallslive/static/css'))
        .pipe(browserSync.reload({stream:true}));
});

// Reload all Browsers
gulp.task('bs-reload', function () {
    browserSync.reload();
});

// Default task to be run with `gulp`
gulp.task('default', ['browser-sync'], function () {
    gulp.watch("smallslive/static/sass/**/*.scss", ['sass']);
    gulp.watch("smallslive/templates/**/*.html", ['bs-reload']);
});
