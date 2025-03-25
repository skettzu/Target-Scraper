import unittest
from sources.poke_bot import TargetPokemonBot

class TestPokeBot(unittest.TestCase):
    def setUp(self):
        self.PokeObj = TargetPokemonBot(target_email="", target_password="", urls= None, test=True)
    # Test tcin extraction
    def test_tcins_extract(self):
        all_url = ["https://www.target.com/p/pokemon-scarlet-violet-s3-5-booster-bundle-box/-/A-88897904", "https://www.target.com/p/2024-pok-scarlet-violet-s8-5-elite-trainer-box/-/A-93954435",
                   "https://www.target.com/p/2025-pokemon-prismatic-evolutions-accessory-pouch-special-collection/-/A-94300053", "https://www.target.com/p/pok-233-mon-trading-card-game-scarlet-38-violet-prismatic-evolutions-booster-bundle/-/A-93954446",
                   "https://www.target.com/p/pok-233-mon-trading-card-game-quaquaval-ex-deluxe-battle-deck/-/A-89542109",
                     "https://www.target.com/p/pok-233-mon-trading-card-game-scarlet-38-violet-8212-journey-together-booster-bundle/-/A-94300074", "https://www.target.com/p/pokemon-trading-card-game-scarlet-38-violet-surging-sparks-booster-bundle/-/A-91619929"]
        self.PokeObj.set_url(all_url)
        test1 = self.PokeObj.extract_tcin_from_url()
        self.assertEqual(test1, "88897904,93954435,94300053,93954446,89542109,94300074,91619929", f"TCINs don't match {test1}")
    # Test in stock
    # Test out of stock