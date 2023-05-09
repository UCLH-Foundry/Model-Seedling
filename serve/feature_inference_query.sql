SELECT top 10 [csn]
    ,[date_of_birth]
    ,[horizon_datetime]
    FROM [dbo].[date_of_birth_v1]
    WHERE [csn] = :csn