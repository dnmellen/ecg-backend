# Testing

You can run the tests with the following command:

```bash
scripts/run_pytest.sh tests
```

This will run the tests and generate a coverage report.

```
---------- coverage: platform linux, python 3.10.13-final-0 ----------
Name                                                          Stmts   Miss  Cover
---------------------------------------------------------------------------------
app/__init__.py                                                   0      0   100%
app/alembic/versions/1b9b576719b8_create_user_models.py          11      1    91%
app/alembic/versions/3dc108746467_add_dataanalysis_model.py      13      2    85%
app/alembic/versions/4e8fcb030194_add_fk_signal.py               13      2    85%
app/alembic/versions/78dd3a319c0b_create_ecg_models.py           17      4    76%
app/alembic/versions/033843a1d580_add_default_for_status.py       9      1    89%
app/alembic/versions/abeea6f3fe52_add_cascade_delete.py           9      1    89%
app/alembic/versions/becb54088400_fix_ecg_id_field.py             9      1    89%
app/alembic/versions/c02de0f9d5e4_add_fk.py                      13      2    85%
app/api/__init__.py                                               0      0   100%
app/api/dependencies/__init__.py                                  0      0   100%
app/api/dependencies/core.py                                      5      0   100%
app/api/dependencies/user.py                                     33     10    70%
app/api/routers/__init__.py                                       0      0   100%
app/api/routers/auth.py                                          21      8    62%
app/api/routers/ecg.py                                           70     14    80%
app/api/routers/users.py                                         13      1    92%
app/config.py                                                    17      0   100%
app/main.py                                                      24      4    83%
app/models/__init__.py                                            4      0   100%
app/models/dal.py                                                41      8    80%
app/models/database.py                                           41     11    73%
app/models/ecg.py                                                53      4    92%
app/models/user.py                                               19      0   100%
app/processors/__init__.py                                       35     14    60%
app/processors/num_crosses_zero.py                               20      0   100%
app/schemas/__init__.py                                           0      0   100%
app/schemas/auth.py                                               7      0   100%
app/schemas/ecg.py                                               48      0   100%
app/schemas/user.py                                              22      1    95%
app/utils/__init__.py                                             0      0   100%
app/utils/auth.py                                                38      8    79%
app/utils/core.py                                                16      1    94%
---------------------------------------------------------------------------------
TOTAL                                                           621     98    84%

24 passed, 1 warning in 16.77s
```