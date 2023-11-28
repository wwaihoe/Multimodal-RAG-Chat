import Image from 'next/image'
import styles from './page.module.css'

import FileLoader from './FileLoader'

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <h1>
          RAG chatbot
        </h1>
        <div>
          <Image
            src="/chatbotLogo.svg"
            alt="Chatbot Logo"
            className={styles.chatbotLogo}
            width={200}
            height={100}
            priority
          />
        </div>
      </div>
      <div className={styles.center}>
        <div className={styles.fileLoader}>
          <FileLoader/>
        </div>
        <div className={styles.chatbox}>
          <p>
            chatbox
          </p>
        </div>
      </div>
    </main>
  )
}
