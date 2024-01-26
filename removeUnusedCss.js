const purify = require('purify-css');
const fs = require('fs');

console.log('Reading HTML file...');

const content = fs.readFileSync('processed.html', 'utf8');
const css = fs.readFileSync('style.css', 'utf8');

const options = {
    output: 'purified.css',
    minify: false,
    info: true
};

console.log('Purifying CSS...');


try {
    purify(content, css, options, function (purifiedResult) {
        console.log('Purification complete. Reading purified CSS...');
        console.log(purifiedResult);
        // Additional logic if needed after successful purification
    });
} catch (error) {
    console.error('An error occurred in the callback:', error);
    console.error('Error stack:', error.stack);
    // Create an empty 'purified.css' file
    fs.writeFileSync(options.output, '');
    console.log('Created an empty purified.css file due to an error.');
}

console.log('Script execution complete.');

