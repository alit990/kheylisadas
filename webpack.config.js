const path = require('path');

module.exports = [
    {
        entry: './assets/scripts/index.js',
        output: {
            path: path.resolve(__dirname, 'core', 'static'),
            filename: 'bundle.js',
        },
        resolve: {
            extensions: ['.js', '.jsx'],
            alias: {
                '@core': path.resolve(__dirname, 'core', 'static'),
            },
        },
    },
    {
        entry: './assets/scripts/index.js',
        output: {
            path: path.resolve(__dirname, 'core', 'static'),
            filename: 'bundle_lib.js',
            library: 'MyLibrary',
            libraryTarget: 'umd',
        },
        resolve: {
            extensions: ['.js', '.jsx'],
            alias: {
                '@core': path.resolve(__dirname, 'core', 'static'),
            },
        },
    },
    {
        entry: './assets/scripts/index_sweetalert.js',
        output: {
            path: path.resolve(__dirname, 'core', 'static'),
            filename: 'bundle_sweetalert.js',
        },
        resolve: {
            extensions: ['.js', '.jsx'],
            alias: {
                '@core': path.resolve(__dirname, 'core', 'static'),
            },
        },
    },
];