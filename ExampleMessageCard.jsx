import { Link } from 'react-router-dom'

function ExampleMessageCard({ message }) {
  const getOlympicsReply = (code) => {
    if (code === 101) return "Events start at 9 AM daily."
    if (code === 202) return "USA is leading the medal table."
    if (code === 303) return "Tickets available on official website."
    return "Sorry, I don't understand."
  }

  return (
    <div>
      <strong><Link to={`/profile/${message.username}`}>{message.username}</Link></strong>
      {' '}
      <small>({new Date(message.created_at).toLocaleString()})</small>
      <small> [#{getOlympicsReply(message.random_number)}]</small>
      {message.image && <><br /><img src={message.image} alt="image" width="64" height="64" /></>}
      <p>{message.content}</p>
      <hr />
    </div>
  )
}

export default ExampleMessageCard