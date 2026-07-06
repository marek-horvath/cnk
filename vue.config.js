const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: process.env.NODE_ENV === 'production' ? '/cnk/' : '/',
  devServer: {
    historyApiFallback: true,
    setupMiddlewares: (middlewares) => {
      middlewares.unshift({
        name: 'admin-fallback',
        middleware: (request, response, next) => {
          if (request.url === '/admin' || request.url.startsWith('/admin/')) {
            request.url = '/'
          }

          next()
        }
      })

      return middlewares
    }
  }
})
