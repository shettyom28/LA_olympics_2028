import { Link } from 'react-router-dom'

function ExampleMessageCard({ message }) {
  return (
    <div>
      <strong><Link to={`/profile/${message.username}`}>{message.username}</Link></strong>
      {' '}
      <small>({new Date(message.created_at).toLocaleString()})</small>
      {message.bot_response && <small> [{message.bot_response}]</small>}
      {message.image && <><br /><img src={message.image} alt="image" width="64" height="64" /></>}
      <p>{message.content}</p>
      <hr />
    </div>
  )
}

export default ExampleMessageCard
