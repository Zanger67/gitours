"use client"

import '@ant-design/v5-patch-for-react-19';
import { useState } from "react"
import { exampleData, downloadJSONFile } from "./exampleText"
import { message } from "antd"
import { GithubFilled, DownloadOutlined, UploadOutlined, LoadingOutlined } from "@ant-design/icons"

export default function page() {
    const [jsonFileText, setJsonFileText] = useState('')
    const [inputLink, setInputLink] = useState('')
    const [progressVisible, setProgressVisible] = useState('hidden')
    const [inputDisabled, setInputDisabled] = useState(false)
    const [downloadDisabled, setDownloadDisabled] = useState(true)
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
                        disabled={inputDisabled}
                        onChange={(e) => {setInputLink(e.target.value)}}
                        type="url"
                        pattern="https://.*"
                        size="50"
                        placeholder="https://github.com/OwnerName/RepoName"
                        required
                    ></input>
                <div className='Summarization Summary'
                    style={{
                        paddingBottom: 10,
                        visibility: progressVisible
                    }}>
                    <h3>Now summarizing GitHub Repo at {inputLink}
                        <LoadingOutlined />
                    </h3>
                </div>
                    <button
                        disabled={inputDisabled}
                        onClick={() => {
                            if (inputLink.startsWith('https://github.com')) {
                                message.info("Summarization in progess. For larger repositories, this process could take multiple minutes.", 6)
                                setProgressVisible('visible')
                                setInputDisabled(true)
                                setDownloadDisabled(true)
                                // Make a request to Python Backend
                                // Example Input Link: https://github.com/indmdev/Free-Telegram-Store-Bot
                                const backEndRoute = `http://localhost:5000/retrieve/${inputLink}`
                                fetch(backEndRoute)
                                    .then(response => response.json()).then(data => {
                                        console.log(data);
                                        console.log(JSON.stringify(data))
                                        setJsonFileText(JSON.stringify(data))
                                        message.success("Summarization Successful");
                                        setProgressVisible('hidden');
                                        setInputDisabled(false);
                                        setDownloadDisabled(false);
                                    })
                                    .catch(error => {
                                        console.log(error);
                                        message.error("An error occurred during summarization");
                                        setProgressVisible('hidden');
                                        setInputDisabled(false);
                                        setDownloadDisabled(false);
                                    });

                            } else {
                                message.error('URL must take the pattern "https://github.com/OwnerName/RepoName"')
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
                        disabled={downloadDisabled}
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