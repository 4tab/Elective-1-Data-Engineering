# Use the .astype() method to convert rental_rate into a string
rental_rate_str = film_df.rental_rate.astype("str")

# Split rental_rate_str on '.' and expand the results into columns
rental_rate_expanded = rental_rate_str.str.split(".", expand=True)

# Assign the newly created columns to film_df
film_df = film_df.assign(
    rental_rate_dollar=rental_rate_expanded[0],
    rental_rate_cents=rental_rate_expanded[1],
)
