const path = require('path');

module.exports =[
    {
    entry: './assets/scripts/index.js',
    output: {
        'path': path.resolve(__dirname, 'core', 'static'),
        'filename': 'bundle.js'
    }
},
      {
    entry: './assets/scripts/index_sweetalert.js',
    output: {
        'path': path.resolve(__dirname, 'core', 'static'),
        'filename': 'bundle_sweetalert.js'
    }
}
    ];