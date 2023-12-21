"use client"

import styles from '../page.module.css' 
import React, { useState } from 'react'
import Image from 'next/image'


interface messageItem {
    sender: string,
    message: string,
  }

function ChatMessage(prop: messageItem) {
    const AIMessage = prop.sender === "AI";

    return (
      <div>
        {AIMessage && (
        <div className={styles.aIMessageDiv}>
          <Image
            src="/chatbotLogo.svg"
            alt="Chatbot Logo"
            className={styles.chatbotLogo}
            width={50}
            height={50}
            priority
          />
          <p className={styles.aIMessage}>
            {prop.message}
          </p>
        </div>
        )}
        {!AIMessage && (
        <div className={styles.humanMessageDiv}>
          <Image
            src="/userIcon.svg"
            alt="User Icon"
            className={styles.userIcon}
            width={30}
            height={30}
            priority
          />
          <p className={styles.humanMessage}>
            {prop.message}
          </p>
        </div>
      )}
      </div>
    )
  }
  
  export default ChatMessage