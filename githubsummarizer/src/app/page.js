"use client"

import { useState } from "react"
import { exampleData, downloadJSONFile } from "./exampleText"

export default function page() {
    const [jsonFileText, setJsonFileText] = useState('')
    const [inputLink, setInputLink] = useState('')
    return (
        <div>
            <div className="header">
                <h1>GitHub Summarizer</h1>
            </div>
            <div className="inputBox">
                <h2>Input link to GitHub Repository to Summarize</h2>
                <div className="linkInput">
                    <input
                        className="textInput"
                        value={inputLink}
                        onChange={(e) => {setInputLink(e.target.value)}}
                        type="url"
                        pattern="https://.*"
                        size="50"
                        placeholder="https://github.com/Owner/RepoName.git"
                        required
                    ></input>
                    <button
                        onClick={() => {
                            if (inputLink.startsWith('https://')) {
                                alert('success')
                                setJsonFileText(JSON.stringify(exampleData))
                            } else {
                                alert('URL must take the pattern "https://*"')
                            }
                        }}
                    >Submit</button>
                    <h2>Output JSON File</h2>
                    <textarea
                        readOnly
                        value={jsonFileText}
                        // value={buildExampleJSON(exampleData.repoName, exampleData.repoOwner, exampleData.link)}
                        rows={10}
                        cols={100}
                        placeholder="JSON Text File Content goes here"
                    ></textarea>
                    <br></br>
                    <button
                        onClick={() => {
                            if (jsonFileText == '') {
                                alert('No JSON file data exists')
                            } else {
                                const jsonFile = new File([JSON.stringify(exampleData)], 'exampleData.json', {type: 'text/plain'})
                                const jsonFileName = 'exampleData.json'
                                downloadJSONFile(jsonFile, jsonFileName)
                            }
                        }}
                    >Download JSON</button>
                </div>
            </div>
        </div>
    )
}