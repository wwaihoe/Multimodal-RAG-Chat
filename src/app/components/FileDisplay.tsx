"use client"

import styles from '../page.module.css'
import React, { useState } from 'react'

interface fileItem {
  name: string,
  size: number,
  type: string
}

function FileDisplay(prop: fileItem) {
  return (
    <div>
      <p>
        {prop.name}
      </p>
    </div>
  )
}

export default FileDisplay