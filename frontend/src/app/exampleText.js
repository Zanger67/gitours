export const exampleData = {
    repoName: 'ExampleRepo',
    repoOwner: 'ExampleOwner',
    link: 'https://github.com/ExampleOwner/ExampleRepo'
}

/**
 * Downloads a JSON file onto the client's device.
 * @param {File} file The file object to be downloaded.
 * @param {String} fileName The name of the download object.
 */
export function downloadJSONFile(file, fileName) {
    const doc = document.createElement('a')
    doc.href = URL.createObjectURL(file)
    doc.download = fileName
    doc.click()
    URL.revokeObjectURL(doc.href)
}