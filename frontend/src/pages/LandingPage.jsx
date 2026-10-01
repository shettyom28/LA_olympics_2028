import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../LandingPage.css';
import LeaderboardTable from '../components/LeaderboardTable';
import api from '../api/client';
import { useAuth } from '../context/useAuth';

const LandingPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = useState(0);

  async function handleLogout() {
    await logout();
    navigate('/');
  }
  const [events, setEvents] = useState([]);
  const [athletes, setAthletes] = useState([]);

  const slides = [
    { img: '/images/Swimming.jpg',  title: 'Swimming Championship', sub: 'Los Angeles Aquatics Centre' },
    { img: '/images/Running.jpg',   title: 'Track & Field',          sub: 'SoFi Stadium' },
    { img: '/images/Gymnastics',    title: 'Gymnastics',             sub: 'Crypto.com Arena' },
    { img: '/images/Freestyle Skiing', title: 'Freestyle Skiing',   sub: 'Mountain venue' },
  ];

  useEffect(() => {
    const t = setInterval(() => setCurrentSlide(p => (p + 1) % slides.length), 4000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    api.get('/api/v1/events/').then(setEvents).catch(() => {});
    api.get('/api/v1/athletes/').then(setAthletes).catch(() => {});
  }, []);

  const upcomingEvents = events.slice(0, 10);
  const featuredAthletes = athletes.slice(0, 10);

  return (
    <div className="landing-page">
      {/* NAVBAR */}
      <nav className="navbar">
        <h2 className="logo">Olympics 2028</h2>
        <ul className="nav-links">
          <li><Link to="/">Home</Link></li>
          <li><Link to="/schedule">Schedule</Link></li>
          <li><Link to="/athletes">Athletes</Link></li>
          <li><Link to="/venues">Venues</Link></li>
          {user ? (
            <>
              <li><Link to={`/profile/${user.username}`}>👤 {user.username}</Link></li>
              <li><button className="nav-logout-btn" onClick={handleLogout}>Logout</button></li>
            </>
          ) : (
            <>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register" className="nav-register-btn">Register</Link></li>
            </>
          )}
        </ul>
      </nav>

      {/* HERO SLIDER */}
      <div className="hero">
        {slides.map((slide, i) => (
          <div key={i} className={`slide ${i === currentSlide ? 'active' : ''}`}>
            <img src={slide.img} alt={slide.title} />
            <div className="overlay">
              <p className="slide-sub">{slide.sub}</p>
              <h1>{slide.title}</h1>
              <Link to="/schedule"><button className="btn">View Schedule</button></Link>
            </div>
          </div>
        ))}
        <span className="arrow left" onClick={() => setCurrentSlide(p => (p - 1 + slides.length) % slides.length)}>❮</span>
        <span className="arrow right" onClick={() => setCurrentSlide(p => (p + 1) % slides.length)}>❯</span>
        <div className="slide-dots">
          {slides.map((_, i) => (
            <button key={i} className={`slide-dot ${i === currentSlide ? 'active' : ''}`} onClick={() => setCurrentSlide(i)} />
          ))}
        </div>
      </div>

      {/* UPCOMING EVENTS */}
      <section className="ld-section">
        <div className="ld-section-header">
          <div>
            <p className="ld-tag">SCHEDULE</p>
            <h2 className="ld-title">Upcoming Events</h2>
          </div>
          <Link to="/schedule" className="ld-see-all">See all →</Link>
        </div>
        {upcomingEvents.length === 0 ? (
          <div className="ld-empty">No events yet — check back soon.</div>
        ) : (
          <div className="ld-scroll-track">
            {upcomingEvents.map(ev => (
              <div key={ev.id} className="ld-event-card">
                <div className="ld-event-top">
                  <div className="ld-event-sport">{ev.sport_name}</div>
                  <h3 className="ld-event-name">{ev.name}</h3>
                  <p className="ld-event-venue">{ev.venue_name}</p>
                  <p className="ld-event-date">
                    {new Date(ev.start_time).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                    &nbsp;·&nbsp;
                    {new Date(ev.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  {ev.athletes_preview?.length > 0 && (
                    <div className="ld-event-athletes">
                      {ev.athletes_preview.map((name, i) => (
                        <span key={i} className="ld-athlete-chip">{name}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="ld-event-actions">
                  <Link to={`/event/${ev.id}`} className="ld-btn-sm">Details</Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* FEATURED ATHLETES */}
      <section className="ld-section ld-section--dark">
        <div className="ld-section-header">
          <div>
            <p className="ld-tag">ATHLETES</p>
            <h2 className="ld-title">Meet the Athletes</h2>
          </div>
          <Link to="/athletes" className="ld-see-all">See all →</Link>
        </div>
        {featuredAthletes.length === 0 ? (
          <div className="ld-empty">No athletes registered yet.</div>
        ) : (
          <div className="ld-scroll-track">
            {featuredAthletes.map(a => (
              <div key={a.id} className="ld-athlete-card">
                <div className="ld-athlete-card-top">
                  <div className="ld-athlete-avatar">
                    {(a.full_name || a.username || '?')[0].toUpperCase()}
                  </div>
                  <h3 className="ld-athlete-name">{a.full_name || a.username}</h3>
                  <p className="ld-athlete-sport">{a.sport_name}</p>
                  <p className="ld-athlete-country">{a.country_name}</p>
                  {a.bio && <p className="ld-athlete-bio">{a.bio.slice(0, 55)}{a.bio.length > 55 ? '…' : ''}</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* TICKETS */}
      <section className="pricing">
        <p className="tag">BOOK NOW</p>
        <h1>GET YOUR TICKETS</h1>
        <p className="subtitle">
          From general admission to VIP packages — be part of Olympic history in Los Angeles.
        </p>
        <div className="pricing-container">
          <div className="price-card">
            <p className="plan">GENERAL</p>
            <h2>STANDARD PASS</h2>
            <h3>$89 <span>/session</span></h3>
            <ul>
              <li>✔ Single session access</li>
              <li>✔ General seating area</li>
              <li>✔ Digital ticket delivery</li>
              <li className="disabled">✖ Lounge access</li>
              <li className="disabled">✖ Athlete meet &amp; greet</li>
            </ul>
            <button className="price-btn">Buy Now</button>
          </div>
          <div className="price-card premium">
            <span className="badge">MOST POPULAR</span>
            <p className="plan">PREMIUM</p>
            <h2>GOLD PACKAGE</h2>
            <h3>$249 <span>/session</span></h3>
            <ul>
              <li>✔ Priority seating</li>
              <li>✔ Olympic Lounge access</li>
              <li>✔ Official merch bundle</li>
              <li>✔ Exclusive fan zone</li>
              <li className="disabled">✖ Athlete meet &amp; greet</li>
            </ul>
            <button className="price-btn">Buy Now</button>
          </div>
        </div>
      </section>

      {/* LEADERBOARD */}
      <section className="leaderboard">
        <p className="lb-tag">MEDAL TABLE</p>
        <h1>LEADERBOARD</h1>
        <p className="lb-sub">Live standings updated after every medal ceremony.</p>
        <LeaderboardTable />
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-container" style={{ display: 'flex', justifyContent: 'space-around' }}>
          <div className="footer-column">
            <h3>QUICK LINKS</h3>
            <ul>
              <li><Link to="/schedule">Schedule</Link></li>
              <li><Link to="/leaderboard">Medal Table</Link></li>
              <li><Link to="/athletes">Athletes</Link></li>
            </ul>
          </div>
          <div className="footer-column">
            <h3>INFORMATION</h3>
            <ul>
              <li><a href="#">About LA 2028</a></li>
              <li><a href="#">Volunteer</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2028 Olympics Los Angeles. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
