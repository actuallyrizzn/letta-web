export const DEFAULT_BOT_MESSAGE =
  'Bootup sequence complete. Persona activated. Testing messaging functionality.'
export const NO_MESSAGES_LABEL = 'Start a chat...'

export const MESSAGE_POPOVER_DESCRIPTION =
  "This is an open source chatbot template built using Letta. Each agent is stateful - so it has long-term memory (it can learn over time) and can be run indefinitely without context window overflow."
export const suggestedChatActions = [
  {
    title: 'Tell me about yourself',
    description: 'Ask the chatbot about its persona',
    action: 'Tell me about yourself'
  },
  {
    title: 'What do you know about me?',
    description: 'Ask the chatbot about its memory of you',
    action: 'What do you know about me?'
  },
  {
    title: 'Today was my birthday!',
    description: 'Tell the chatbot something memorable',
    action:
      'Today was my birthday! My mom Brenda made me chocolate cake, my favorite :D'
  },
  {
    title: 'Explain your memory system to me',
    description: 'Ask the chatbot about its inner workings',
    action: 'Explain your memory system to me'
  }
]

export const TEXTBOX_PLACEHOLDER = 'Send a message...'

export const ERROR_CONNECTING =
  'Issue loading data. Please check your connection to the Letta Server.'
