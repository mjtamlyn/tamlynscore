const webpack = require('webpack');
const path = require('path');

const BundleTracker = require('webpack-bundle-tracker');

const devMode = process.env.NODE_ENV !== 'production';
const devModeServer = 'http://localhost:8080';

const config = {
    entry: './js_src/index.js',
    mode: devMode ? 'development' : 'production',
    output: {
        path: __dirname,
        filename: 'bundles/bundle.js',
        publicPath: devMode ? `${devModeServer}/bundles/` : undefined,
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                use: 'babel-loader',
                exclude: /node_modules/
            }
        ]
    },
    plugins: [
        new BundleTracker({ filename: 'build/webpack-stats.json' }),
    ],
    devServer: {
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization",
        },
    },
};

module.exports = config;
