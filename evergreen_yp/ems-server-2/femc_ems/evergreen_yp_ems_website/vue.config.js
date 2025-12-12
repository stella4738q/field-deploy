const { defineConfig } = require('@vue/cli-service')
const TerserPlugin = require('terser-webpack-plugin');
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave:false,
    devServer: {
      https:false,
      historyApiFallback: true,
      allowedHosts: "all",
      port: process.env.VUE_APP_Port,
      proxy: {
        "^/api": {
          target: process.env.VUE_APP_ApiURL_Proxy,
          ws: false,
          changeOrigin: true,
          pathRewrite: {                         
            '^/api': '', 
          }
        },
      }
  },
  productionSourceMap: true,
  configureWebpack: {
    devtool: 'source-map', // This option ensures source maps are generated
    optimization: {
      minimize: true,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: true, // Prevents the removal of console logs
              drop_debugger: true,
            },
          },
        }),
      ],
    },
  }
})
