import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import NewsSentiment from './components/NewsSentiment';
import './styles.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route exact path="/" component={Dashboard} />
          <Route path="/news-sentiment" component={NewsSentiment} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
