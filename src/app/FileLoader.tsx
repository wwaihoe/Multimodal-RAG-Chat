"use client"

import styles from './page.module.css'
import React, { useState } from 'react'

import FileDisplay from './FileDisplay'

interface fileItem {
  name: string,
  size: number,
  type: string
}

function FileLoader() {
  const [selectedFile, setSelectedFile] = useState<fileItem | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<fileItem[] | []>([])
  const fileList = uploadedFiles.map((fileToDisplay) =>
    <FileDisplay key={fileToDisplay.name} name={fileToDisplay.name} size={fileToDisplay.size} type={fileToDisplay.type}/>
  )
  const handleFileChange = (event: React.ChangeEvent) => {
    // Get the selected file from the input
    const target = event.target as HTMLInputElement
    if (target && target?.files?.[0]) {
      const file = target.files[0]
      setSelectedFile(file)
    }
  }
  const handleUpload = () => {
    // Handle the file upload logic here, for example, send the file to a server
    if (selectedFile) {
      let sameName = false
      for (const uploadedFile of uploadedFiles) {
        if (selectedFile.name === uploadedFile.name) {
          alert('A file with the same name has already been uploaded')
          sameName = true
          break
        }
      }
      if (!sameName) {
        // You can perform actions like uploading the file to a server here
        console.log('Uploading file:', selectedFile)
        const newFile: fileItem = {"name": selectedFile.name, 
          "size": selectedFile.size,
          "type": selectedFile.type
        }
        setUploadedFiles([...uploadedFiles, newFile])
      }
      // Reset the selectedFile state after uploading
      setSelectedFile(null)
      const fileInput = document.getElementById('fileInput') as HTMLInputElement
      if (fileInput) {
        fileInput.value = ''
      }
    } else {
      console.log('No file selected')
    }
    console.log(uploadedFiles)
  }
  const handleDelete = (fileName: string) => {
    if (uploadedFiles.length > 0) {
      setUploadedFiles(uploadedFiles.filter(item => item.name !== fileName))
    }
  }
  return (
    <div>
      <div>
        <h3>
          Upload text file for knowledge base
        </h3>
        <input type="file" id="fileInput" onChange={handleFileChange} />
          <button onClick={handleUpload}>Upload</button>
            {selectedFile && (
              <div>
                <p>Selected File: {selectedFile.name}</p>
                <p>File Size: {selectedFile.size} bytes</p>
              </div>
            )}
      </div>
      <div>
        <h3>
          Files in Knowledge Base
        </h3>
        <ul>
          {fileList}
        </ul>
      </div>
    </div>
  )
}

export default FileLoader