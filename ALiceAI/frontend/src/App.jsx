import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setUserData } from './redux/userSlice';
import Home from './pages/Home';
import getCurrentUser from './features/getCurrentUser';

function App() {

  const dispatch = useDispatch()
  useEffect(() => {
    const getUser = async () => {
      const user = await getCurrentUser()
      dispatch(setUserData(user))
    }
    getUser()
  }, [dispatch])
  
  return (
    <>
      <Home />
    </>
  )
}

export default App