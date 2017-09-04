var path = require("path")
var webpack = require('webpack')

module.exports = {
  context: __dirname,

  entry: './tmdb/static/js/src/index.jsx',

  output: {
      path: './tmdb/static/js/',
      filename: "bundle.js",
  },

  externals: [
  ], // add all vendor libs

  plugins: [
    new webpack.optimize.CommonsChunkPlugin({name: 'vendors', filename: 'vendors.js'}),
  ], // add all common plugins here

  module: {
    loaders: [
        { test: /\.js$/, loader: 'babel-loader', exclude: /node_modules/ },
        { test: /\.jsx$/, loader: 'babel-loader', exclude: /node_modules/ }
    ] // add all common loaders here
  },

  resolve: {
//    modulesDirectories: ['node_modules', 'bower_components'],
//    extensions: ['', '.js', '.jsx']
  },
}