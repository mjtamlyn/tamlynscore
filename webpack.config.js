const webpack = require('webpack');
const path = require('path');

const BundleTracker = require('webpack-bundle-tracker');

const devMode = process.env.NODE_ENV !== 'production';
const devModeServer = 'http://localhost:8080';

const config = {
    entry: {
        'score_sheet': './js_src/scoreSheet.js',
        'target_input': './js_src/targetInput.js',
        'target_list': './js_src/targetList.js'
    },
    mode: devMode ? 'development' : 'production',
    output: {
        filename: devMode ? '[name].js' : '[name]-[contenthash].js',
        path: path.resolve(__dirname, 'build/bundles'),
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
        new BundleTracker({
            path: path.resolve(__dirname, 'build'),
            filename: 'webpack-stats.json'
        }),
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
