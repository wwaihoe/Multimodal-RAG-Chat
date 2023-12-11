"use client"

import styles from '../page.module.css'
import React, { useState } from 'react'

interface fileItem {
  name: string,
  size: number,
  type: string
}

interface fileDisplayProps extends fileItem {
  removeFunction: (fileName: string) => void 
}

function FileDisplay(prop: fileDisplayProps) {
  return (
    <div>
      <p>
        {prop.name}
      </p>
      <button onClick={() => prop.removeFunction(prop.name)}>
        Remove file
      </button>
    </div>
  )
}

export default FileDisplay