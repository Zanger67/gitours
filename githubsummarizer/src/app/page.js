"use client"

import '@ant-design/v5-patch-for-react-19';
import { useState } from "react"
import { exampleData, downloadJSONFile } from "./exampleText"
import { message } from "antd"
import { GithubFilled, DownloadOutlined, UploadOutlined } from "@ant-design/icons"

export default function page() {
    const [jsonFileText, setJsonFileText] = useState('')
    const [inputLink, setInputLink] = useState('')
    return (
        <div>
            <div className="header">
                <GithubFilled style={{fontSize: 50}}/>
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
                                message.success('Summarization Successful')
                                setJsonFileText(JSON.stringify(exampleData))
                            } else {
                                message.error('URL must take the pattern "https://*"')
                            }
                        }}
                    >
                        <UploadOutlined style={{marginRight: 5}}/>
                        Submit
                        </button>
                    <h2>Output JSON File</h2>
                    <textarea
                        readOnly
                        value={jsonFileText}
                        rows={10}
                        cols={100}
                        placeholder="JSON Text File Content goes here"
                    ></textarea>
                    <br></br>
                    <button
                        onClick={() => {
                            if (jsonFileText == '') {
                                message.error('No JSON file data exists')
                            } else {
                                const jsonFile = new File([JSON.stringify(exampleData)], 'exampleData.json', {type: 'text/plain'})
                                const jsonFileName = 'exampleData.json'
                                downloadJSONFile(jsonFile, jsonFileName)
                            }
                        }}
                    >
                        <DownloadOutlined style={{marginRight: 5}}/>
                        Download JSON
                    </button>
                </div>
            </div>
        </div>
    )
}