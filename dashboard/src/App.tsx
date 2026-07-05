import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Shell } from './components/Shell';
import { Adoption } from './views/Adoption';
import { Context } from './views/Context';
import { Leaderboard } from './views/Leaderboard';
import { NotFound } from './views/NotFound';
import { Overview } from './views/Overview';
import { Registry } from './views/Registry';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Shell />}>
          <Route path="/" element={<Overview />} />
          <Route path="/registry" element={<Registry />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/adoption" element={<Adoption />} />
          <Route path="/context" element={<Context />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
