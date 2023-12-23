"use client"

import styles from '../page.module.css'
import React, { useState } from 'react'

interface fileItem {
  name: string,
  size: number
}

interface fileDisplayProps extends fileItem {
  removeFunction: (fileName: string) => void 
}

function FileDisplay(prop: fileDisplayProps) {
  return (
    <div className={styles.fileDisplay}>
      <p className={styles.fileName}>
        {prop.name}
      </p>
      <button className={styles.removeFileButton} onClick={() => prop.removeFunction(prop.name)}>
        Remove
      </button>
    </div>
  )
}

export default FileDisplay