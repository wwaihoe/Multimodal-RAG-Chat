"use client"

import styles from '../page.module.css'
import React, { useState, useEffect } from 'react'

import FileDisplay from './FileDisplay'

interface fileItem {
  name: string,
  size: number
}

const retrievalModelURL = "localhost"
const retrievalModelPort = "8002"
const acceptedFileExtensions = ["pdf", "jpeg", "jpg", "png"]


function FileLoader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<fileItem[] | []>([])

  useEffect(() => {
    loadFiles()
  }, [])

  const loadFiles = async() => {
    try{
      const response = await fetch(`http://${retrievalModelURL}:${retrievalModelPort}/load`, {
            method: 'GET'
          })
      if (response.ok) {
        console.log("Successfully loaded files")
        const responseJSON = await response.json()
        const fileList = responseJSON.files
        console.log(fileList)
        if (fileList.length > 0) {
          setUploadedFiles(fileList)
        }
      }
      else {
        alert("Failed to load files")
      }
    }
    catch(err) {
      console.log(err)
      alert("Failed to load files")
    }
  } 

  const handleFileChange = (event: React.ChangeEvent) => {
    const target = event.target as HTMLInputElement
    if (target && target?.files && target?.files?.[0]) {
      const file = target.files[0]
      const fileName = file.name
      const fileExtension = fileName.split('.')?.pop()?.toLowerCase()
      if (fileExtension && acceptedFileExtensions.includes(fileExtension)) {
        setSelectedFile(file)
      }
      else {
        alert("Invalid file type. Accepted file types are: pdf, jpeg, jpg, png")
      }
      target.value = ''
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
      uploadButton.disabled = true
      const loader = document.getElementById("loaderFileUpload") as HTMLDivElement;
      loader.style.display = "inline-block";
      if (!sameName) {
        console.log("Uploading file:", selectedFile)
        const form = new FormData();
        form.append("file", selectedFile);
        try{
          const response = await fetch(`http://${retrievalModelURL}:${retrievalModelPort}/upload`, {
                method: 'POST',
                body: form
              })
          if (response.ok) {
            console.log("Successfully uploaded file:", selectedFile)
            const newFile: fileItem = {
              "name": selectedFile.name, 
              "size": selectedFile.size
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
      //const fileInput = document.getElementById('fileInput') as HTMLInputElement
      //fileInput.value = ''
      uploadButton.disabled = false
      loader.style.display = "none";
    } else {
      alert("No file selected")
    }
  }

  const handleDelete = async (fileName: string) => {
    try {
      const body = {
        "fileName": fileName
      }
      const JSONBody = JSON.stringify(body)
      const response = await fetch(`http://${retrievalModelURL}:${retrievalModelPort}/remove`, {
        method: 'POST',
        headers: {
          "Content-type": "application/json"
        },
        body: JSONBody
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
    <FileDisplay removeFunction={handleDelete} key={fileToDisplay.name} name={fileToDisplay.name} size={fileToDisplay.size}/>
  )

  return (
    <div className={styles.fileLoader}>
      {uploadedFiles.length>0 && (
      <div className={styles.fileList}>
        <h3>
          Files in knowledge base
        </h3>
        <ul>
          {fileList}
        </ul>
      </div>
      )}
      <div id="loaderFileUpload" className="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
      <div>
        <h3>
          Upload PDF file to knowledge base
        </h3>
        <label htmlFor="fileInput" className="custom-file-input">
          Choose file 
        </label>
        <input type="file" id="fileInput" accept=".pdf,.jpeg,.jpg,.png" onChange={handleFileChange} />
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