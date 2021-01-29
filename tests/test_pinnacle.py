def test_game_id(testpinnacle):
    id_ = 1249774441
    url1 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
    url2 = "https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441/"

    pin = testpinnacle
    assert int(pin._game_id(url1)) == id_
    assert int(pin._game_id(url2)) == id_


# Test requires NEW game link
# def test_game(testpinnacle):
#     data = testpinnacle.game(
#         url="https://www.pinnacle.com/en/basketball/nba/detroit-pistons-vs-cleveland-cavaliers/1249774441"
#     )
#     print(data)


def test_build_props(pinnaclegame):
    pinnaclegame.build_props()
