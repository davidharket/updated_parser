const purify = require('purify-css');
const fs = require('fs');

console.log('Reading HTML file...');

const args = process.argv;
const content = args[2];
const css = args[3];


const options = {
    output: 'purified.css',
    minify: false,
    info: true
};

console.log('Purifying CSS...');
try {
    purify(content, css, options, function (purifiedResult) {
        console.log('Purification complete. Reading purified CSS...');
    });
} catch (error) {
    console.error('An error occurred in the callback:', error);
    console.error('Error stack:', error.stack);
}

console.log('Script execution complete.');