import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import NewsSentiment from './components/NewsSentiment';
import PortfolioInsights from './components/PortfolioInsights';
import './styles.css';
import MarketSentiments from "./components/MarketSentiments";

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route exact path="/" component={Dashboard} />
          <Route path="/news-sentiment" component={NewsSentiment} />
          <Route path="/market-sentiment" component={MarketSentiments} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
