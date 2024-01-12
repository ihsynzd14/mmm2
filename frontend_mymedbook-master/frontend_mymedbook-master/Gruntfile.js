module.exports = function (grunt) {

  grunt.initConfig({
    bower_concat: {
      all: {
        dest: {
          'js': 'public/build/_bower.js',
          'css': 'public/build/_bower.css'
        },
        mainFiles: {
          'angular-ui':['build/angular-ui.min.css','build/angular-ui.min.js'],
          bootstrap: ['dist/css/bootstrap.min.css', 'dist/js/bootstrap.min.js'],
        },
        bowerOptions: {
          relative: false
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-bower-concat');
  grunt.registerTask('default', ['bower_concat']);
};
