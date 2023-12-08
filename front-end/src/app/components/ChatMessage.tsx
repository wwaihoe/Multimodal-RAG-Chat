"use client"

import styles from '../page.module.css' 
import React, { useState } from 'react'


interface messageItem {
    sender: string,
    message: string,
  }

function ChatMessage(prop: messageItem) {
    return (
      <div className={styles.chatMessage}>
        <h3>
          {prop.sender}:
        </h3>
        <p>
          {prop.message}
        </p>
      </div>
    )
  }
  
  export default ChatMessage