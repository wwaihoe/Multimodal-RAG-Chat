"use client"

import styles from '../page.module.css'
import React, { useState } from 'react'

import FileDisplay from './FileDisplay'

interface fileItem {
  name: string,
  size: number,
  type: string
}

const chatModelURL = "localhost"
const chatModelPort = "8080"

function FileLoader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<fileItem[] | []>([])

  const handleFileChange = (event: React.ChangeEvent) => {
    const target = event.target as HTMLInputElement
    if (target && target?.files?.[0]) {
      const file = target.files[0]
      setSelectedFile(file)
    }
  }

  const handleUpload = async() => {
    if (selectedFile) {
      let sameName = false
      for (const uploadedFile of uploadedFiles) {
        if (selectedFile.name === uploadedFile.name) {
          alert("A file with the same name has already been uploaded")
          sameName = true
          break
        }
      }
      const uploadButton = document.getElementById("uploadButton") as HTMLButtonElement;
      if (uploadButton) {
        uploadButton.disabled = true
      }
      const loader = document.getElementById("loadingAnimation");
      if (loader) {
        loader.style.display = "block";
      }
      if (!sameName) {
        console.log("Uploading file:", selectedFile)
        const form = new FormData();
        form.append("file", selectedFile);
        try{
          const response = await fetch(`http://${chatModelURL}:${chatModelPort}/upload`, {
                method: 'POST',
                body: form
              })
          console.log(response.status)
          if (response.ok) {
            console.log("Successfully uploaded file:", selectedFile)
            const newFile: fileItem = {"name": selectedFile.name, 
              "size": selectedFile.size,
              "type": selectedFile.type
            }
            setUploadedFiles([...uploadedFiles, newFile])
          }
          else {
            alert("Failed to upload file")
          }
        }
        catch(err) {
          console.log(err)
          alert("Failed to upload file")
        }
      }
      setSelectedFile(null)
      const fileInput = document.getElementById('fileInput') as HTMLInputElement
      if (fileInput) {
        fileInput.value = ''
      }
      if (uploadButton) {
        uploadButton.disabled = false
      }
      if (loader) {
        loader.style.display = "none";
      }
    } else {
      alert("No file selected")
    }
  }

  const handleDelete = async (fileName: string) => {
    try {
      const response = await fetch(`http://${chatModelURL}:${chatModelPort}/remove`, {
        method: 'POST',
        body: fileName
      })
      if (response.ok) {
        setUploadedFiles(uploadedFiles.filter(item => item.name !== fileName))
      }
    }
    catch(err) {
      console.log(err)
    }
  }

  const fileList = uploadedFiles.map((fileToDisplay) =>
    <FileDisplay removeFunction={handleDelete} key={fileToDisplay.name} name={fileToDisplay.name} size={fileToDisplay.size} type={fileToDisplay.type}/>
  )

  return (
    <div className={styles.fileLoader}>
      {uploadedFiles.length>0 && (
      <div>
        <h3>
          Files in knowledge base
        </h3>
        <ul>
          {fileList}
        </ul>
        <div id="loadingAnimation" className="loader"></div>
      </div>
      )}
      <div>
        <h3>
          Upload text file for knowledge base
        </h3>
        <label htmlFor="fileInput" className="custom-file-input">
          Choose file 
        </label>
        <input type="file" id="fileInput" onChange={handleFileChange} />
          <button id="uploadButton" onClick={handleUpload}>Upload</button>
            {selectedFile && (
              <div>
                <p>Selected File: {selectedFile.name}</p>
                <p>File Size: {selectedFile.size} bytes</p>
              </div>
            )}
      </div>
    </div>
  )
}

export default FileLoader